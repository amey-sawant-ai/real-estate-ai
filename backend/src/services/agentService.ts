import axios, { AxiosError } from 'axios';
import logger from '@/utils/logger';

const AGENTS_BASE_URL = process.env.AGENTS_URL || 'http://localhost:8000';

interface AnalysisRequest {
	query: string;
	budget: string;
	risk: string;
}

interface AnalysisResponse {
	[key: string]: unknown;
}

/**
 * Run analysis through the Python agent service.
 *
 * @param query - The user's investment query
 * @param budget - Budget constraints
 * @param risk - Risk profile (low, medium, high)
 * @returns Full response data from the Python service
 * @throws Error if Python service is unreachable or request fails
 */
export async function runAnalysis(
	query: string,
	budget: string,
	risk: string,
): Promise<AnalysisResponse> {
	try {
		logger.info(`Initiating analysis: query="${query.slice(0, 50)}..." budget="${budget}" risk="${risk}"`);

		const payload: AnalysisRequest = { query, budget, risk };

		const response = await axios.post<AnalysisResponse>(
			`${AGENTS_BASE_URL}/analyze`,
			payload,
			{
				timeout: 120000, // 120 second timeout
				headers: {
					'Content-Type': 'application/json',
				},
			},
		);

		logger.info('Analysis completed successfully');
		return response.data;
	} catch (error: unknown) {
		const axiosError = error as AxiosError;

		// Handle connection refused (Python service down)
		if (axiosError.code === 'ECONNREFUSED') {
			logger.error(`Python agent service unavailable at ${AGENTS_BASE_URL}`);
			throw new Error(
				`Agent service is currently unavailable. Please try again later. (Connection refused)`,
			);
		}

		// Handle timeout
		if (axiosError.code === 'ECONNABORTED') {
			logger.error(`Request to Python agent service timed out after 120s`);
			throw new Error('Agent service request timed out. Please try again with a simpler query.');
		}

		// Handle HTTP errors
		if (axiosError.response) {
			const status = axiosError.response.status;
			const message =
				(axiosError.response.data as Record<string, unknown>)?.error || 'Unknown error';

			logger.error(`Python agent service returned status ${status}: ${message}`);
			throw new Error(`Agent service error (${status}): ${message}`);
		}

		// Handle other errors
		logger.error(`Failed to reach Python agent service: ${axiosError.message}`);
		throw new Error(
			`Unable to reach agent service. Please ensure the Python backend is running on ${AGENTS_BASE_URL}`,
		);
	}
}

/**
 * Check if the Python agent service is online.
 *
 * @returns true if service is reachable, false otherwise
 */
export async function isPythonServiceOnline(): Promise<boolean> {
	try {
		const response = await axios.get(`${AGENTS_BASE_URL}/ping`, {
			timeout: 5000, // 5 second timeout for health check
		});
		return response.status === 200;
	} catch (error) {
		logger.warn(`Python agent service health check failed`);
		return false;
	}
}
