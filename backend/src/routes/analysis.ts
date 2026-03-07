import { Router, Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { runAnalysis } from '@/services/agentService';
import logger from '@/utils/logger';

const router = Router();

// Validation schema for analysis request
const AnalysisSchema = z.object({
	query: z.string().min(1, 'Query cannot be empty'),
	budget: z.string().min(1, 'Budget is required'),
	risk: z.enum(['low', 'medium', 'high'], {
		errorMap: () => ({ message: 'Risk must be one of: low, medium, high' }),
	}),
});

type AnalysisInput = z.infer<typeof AnalysisSchema>;

/**
 * POST /api/v1/analyze
 * Execute AI analysis for a real estate investment query.
 *
 * Request body:
 * {
 *   "query": "I want to invest in Mumbai",
 *   "budget": "$100,000",
 *   "risk": "medium"
 * }
 *
 * Response: Full analysis from Python agent service
 */
router.post('/', async (req: Request, res: Response, next: NextFunction): Promise<void> => {
	try {
		// Validate request body
		let payload: AnalysisInput;
		try {
			payload = AnalysisSchema.parse(req.body);
		} catch (validationError) {
			const zodError = validationError as z.ZodError;
			logger.warn(`Validation error: ${zodError.message}`);
			res.status(400).json({
				success: false,
				error: 'Invalid request body',
				details: zodError.errors.map((err) => ({
					field: err.path.join('.'),
					message: err.message,
				})),
			});
			return;
		}

		logger.info(
			`Analysis request received: query="${payload.query.slice(0, 50)}..." budget="${payload.budget}" risk="${payload.risk}"`,
		);

		// Call agent service
		const analysis = await runAnalysis(payload.query, payload.budget, payload.risk);

		logger.info('Analysis response sent to client');
		res.status(200).json({
			success: true,
			data: analysis,
			timestamp: new Date().toISOString(),
		});
	} catch (error: unknown) {
		const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
		logger.error(`Analysis failed: ${errorMessage}`);

		// Check if error is due to agent service being down
		if (
			errorMessage.includes('unavailable') ||
			errorMessage.includes('Connection refused') ||
			errorMessage.includes('Unable to reach')
		) {
			res.status(503).json({
				success: false,
				error: 'Agent service unavailable',
				message: errorMessage,
				timestamp: new Date().toISOString(),
			});
			return;
		}

		// For other errors, return 400 or 500 depending on error type
		if (errorMessage.includes('timed out')) {
			res.status(504).json({
				success: false,
				error: 'Request timeout',
				message: errorMessage,
				timestamp: new Date().toISOString(),
			});
			return;
		}

		// Pass to error handler middleware for unexpected errors
		next(error);
	}
});

export default router;
