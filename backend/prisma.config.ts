import { defineConfig } from 'prisma/config';
import * as dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
    // earlyAccess: true,
    schema: 'prisma/schema.prisma',
    migrations: {
        path: 'prisma/migrations',
    },
    datasource: {
        url: process.env.DATABASE_URL!,
    },
});
