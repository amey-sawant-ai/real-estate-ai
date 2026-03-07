import { Server as HttpServer } from 'http';
import { Server, Socket } from 'socket.io';
import logger from '@/utils/logger';
import config from '@/config/environment';

export let io: Server | null = null;

export const initializeSocket = (server: HttpServer): Server => {
    io = new Server(server, {
        cors: {
            origin: config.clientUrl,
            credentials: true,
        },
    });

    io.on('connection', (socket: Socket) => {
        logger.info(`Socket connected: ${socket.id}`);

        socket.on('disconnect', () => {
            logger.info(`Socket disconnected: ${socket.id}`);
        });

        // Add custom socket event listeners here
        // Example: socket.on('message', (data) => { ... });
    });

    return io;
};
