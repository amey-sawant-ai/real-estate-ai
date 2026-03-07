import dotenv from 'dotenv';
import app from './app';

import config from '@/config/environment';
import { connection as redisConnection } from '@/utils/queue';
import prisma from '@/config/prisma';
import { initializeSocket } from '@/socket';
import logger from '@/utils/logger';

dotenv.config();

const startServer = async (): Promise<void> => {
	try {
		await prisma.$connect();
		logger.info('Connected to PostgreSQL successfully.');

		const server = app.listen(config.port, () => {
			logger.info(
				`Server running in ${config.env} mode at http://${config.host}:${config.port}`,
			);
		});

		// Set server timeout to 120 seconds for long-running agent analysis
		server.setTimeout(120000);

		// Initialize process-wide Socket.io server
		initializeSocket(server);

		const shutdown = async (signal: string): Promise<void> => {
			logger.info(`${signal} received. Shutting down gracefully...`);

			server.close(async () => {
				// Only disconnect Redis if it was successfully connected
				if (redisConnection.status === 'ready') {
					await redisConnection.quit();
				}
				await prisma.$disconnect();
				logger.info('Server and Database disconnected.');
				process.exit(0);
			});

			setTimeout(() => {
				logger.error('Forced shutdown after timeout');
				process.exit(1);
			}, 10000);
		};

		process.on('SIGINT', () => shutdown('SIGINT'));
		process.on('SIGTERM', () => shutdown('SIGTERM'));
	} catch (error) {
		logger.error('Failed to start server:', error as any);
		process.exit(1);
	}
};

startServer();
