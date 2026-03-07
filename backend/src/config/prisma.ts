import { PrismaClient } from '@prisma/client';
import config from './environment';

const prismaClientSingleton = () => {
    return new PrismaClient({
        log: config.isDevelopment ? ['query', 'error', 'warn'] : ['error'],
    });
};

declare global {
    // eslint-disable-next-line no-var
    var prismaGlobal: undefined | ReturnType<typeof prismaClientSingleton>;
}

const prisma = globalThis.prismaGlobal ?? prismaClientSingleton();

export default prisma;

if (process.env.NODE_ENV !== 'production') globalThis.prismaGlobal = prisma;
