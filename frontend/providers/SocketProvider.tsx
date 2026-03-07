'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:4000';

interface SocketContextProps {
    socket: Socket | null;
    isConnected: boolean;
}

const SocketContext = createContext<SocketContextProps>({
    socket: null,
    isConnected: false,
});

export const useSocket = () => {
    return useContext(SocketContext);
};

export const SocketProvider = ({ children }: { children: React.ReactNode }) => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // Initialize socket connection
        const socketInstance = io(SOCKET_URL, {
            withCredentials: true,
            transports: ['websocket', 'polling'], // Prefer websocket
        });

        socketInstance.on('connect', () => {
            console.log('Connected to socket server');
            setIsConnected(true);
        });

        socketInstance.on('disconnect', () => {
            console.log('Disconnected from socket server');
            setIsConnected(false);
        });

        setSocket(socketInstance);

        // Cleanup on unmount
        return () => {
            socketInstance.disconnect();
        };
    }, []);

    return (
        <SocketContext.Provider value={{ socket, isConnected }}>
            {children}
        </SocketContext.Provider>
    );
};
