import { Queue, Worker, QueueEvents, Job } from 'bullmq';
import IORedis from 'ioredis';
import config from '@/config/environment';
import logger from '@/utils/logger';

// Create a reusable Redis connection for BullMQ
// lazyConnect: true means we don't connect until first use
export const connection = new IORedis(config.redisUrl, {
    maxRetriesPerRequest: null, // Required by BullMQ
    lazyConnect: true,
    retryStrategy: (times: number) => {
        // Retry max 3 times with exponential backoff, then give up
        if (times > 3) {
            logger.warn('Redis is unavailable. BullMQ queues will not process until Redis is connected.');
            return null; // Stop retrying
        }
        return Math.min(times * 1000, 3000); // 1s, 2s, 3s
    },
    enableOfflineQueue: false, // Don't queue commands when disconnected
});

connection.on('error', (err) => {
    // Only log ECONNREFUSED once, not repeatedly
    if ((err as any).code === 'ECONNREFUSED') {
        logger.warn(`Redis unavailable at ${config.redisUrl}. BullMQ is disabled until Redis starts.`);
    } else {
        logger.error('Redis connection error:', err);
    }
});

connection.on('connect', () => {
    logger.info('Connected to Redis for BullMQ');
});

// Helper to create a new queue
export const createQueue = (queueName: string) => {
    return new Queue(queueName, { connection });
};

// Helper to create a worker for a queue
export const createWorker = <T = any, R = any>(
    queueName: string,
    processor: (job: Job<T, R>) => Promise<R>,
) => {
    const worker = new Worker<T, R>(queueName, processor, { connection });

    worker.on('completed', (job: Job) => {
        logger.info(`Job ${job.id} completed successfully in queue ${queueName}`);
    });

    worker.on('failed', (job: Job | undefined, err: Error) => {
        logger.error(`Job ${job?.id} failed with error ${err.message} in queue ${queueName}`);
    });

    return worker;
};

// Helper to monitor global queue events
export const createQueueEvents = (queueName: string) => {
    return new QueueEvents(queueName, { connection });
};
