import { Router, Request, Response, NextFunction } from 'express';

const router = Router();

const AGENTS_BASE_URL = process.env.AGENTS_URL || 'http://localhost:8000';

/**
 * POST /api/query
 * Accepts a user query, forwards it to the Python agent, and returns the result.
 * For now this echoes back the agent response (to be expanded with real agent logic).
 */
router.post('/', async (req: Request, res: Response, next: NextFunction) => {
    try {
        const { query } = req.body as { query?: string };

        if (!query || typeof query !== 'string' || !query.trim()) {
            return res.status(400).json({
                success: false,
                error: 'A non-empty "query" string is required in the request body.',
            });
        }

        // Forward query to the Python agent service
        const response = await fetch(`${AGENTS_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query.trim() }),
        });

        // If agent has no /query endpoint yet, echo the query back as a placeholder
        if (!response.ok) {
            return res.status(200).json({
                success: true,
                source: 'echo',
                query: query.trim(),
                result: `Echo: "${query.trim()}" — Agent /query endpoint not yet implemented.`,
            });
        }

        const data = await response.json() as Record<string, unknown>;
        return res.status(200).json({ success: true, source: 'agent', ...data });
    } catch (err: any) {
        if (err.cause?.code === 'ECONNREFUSED') {
            // Agent is offline — echo back the query gracefully
            const { query } = req.body as { query?: string };
            return res.status(200).json({
                success: true,
                source: 'echo',
                query: query?.trim(),
                result: `Echo: "${query?.trim()}" — Agent service is offline.`,
            });
        }
        return next(err);
    }
});

export default router;
