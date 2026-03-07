import { Router, Request, Response } from 'express';
import userRoutes from './user.routes';
import agentsRoutes from './agents.routes';
import queryRoutes from './query.routes';
import analysisRoutes from './analysis';
import { isPythonServiceOnline } from '@/services/agentService';
import logger from '@/utils/logger';

const router = Router();

// Health check with Python service status
router.get('/health', async (_req: Request, res: Response) => {
	try {
		const pythonOnline = await isPythonServiceOnline();
		return res.status(200).json({
			node: 'online',
			python: pythonOnline ? 'online' : 'offline',
			timestamp: new Date().toISOString(),
		});
	} catch (error) {
		logger.error(`Health check error: ${error instanceof Error ? error.message : 'Unknown error'}`);
		return res.status(200).json({
			node: 'online',
			python: 'offline',
			timestamp: new Date().toISOString(),
		});
	}
});

// Route groups
router.use('/users', userRoutes);
router.use('/agents', agentsRoutes);  // → GET /api/v1/agents/ping
router.use('/query', queryRoutes);    // → POST /api/v1/query
router.use('/analyze', analysisRoutes); // → POST /api/v1/analyze

export default router;
