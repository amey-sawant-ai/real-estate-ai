import { Router, Request, Response, NextFunction } from 'express';

const router = Router();

const AGENTS_BASE_URL = process.env.AGENTS_URL || 'http://localhost:8000';

/**
 * GET /api/agents/ping
 * Proxies to the Python agent service to verify it's alive.
 */
router.get('/ping', async (_req: Request, res: Response, next: NextFunction) => {
    try {
        const response = await fetch(`${AGENTS_BASE_URL}/ping`);

        if (!response.ok) {
            return res.status(response.status).json({
                success: false,
                error: `Agent service responded with status ${response.status}`,
            });
        }

        const data = await response.json();
        return res.status(200).json({ success: true, agent: data });
    } catch (err: any) {
        if (err.cause?.code === 'ECONNREFUSED') {
            return res.status(503).json({
                success: false,
                error: 'Agent service is not reachable. Is the Python server running on port 8000?',
            });
        }
        return next(err);
    }
});

export default router;
