import { Request, Response, NextFunction } from 'express';
import ApiError from '@/utils/ApiError';
import { Constants } from '@/config/constants';

// Paths to silently ignore (no error logging, just 404)
const SILENT_NOT_FOUND = ['/favicon.ico', '/robots.txt'];

export const notFoundHandler = (
	req: Request,
	res: Response,
	next: NextFunction,
): void => {
	if (SILENT_NOT_FOUND.includes(req.path)) {
		res.status(404).end();
		return;
	}
	next(
		new ApiError(
			Constants.HTTP_STATUS.NOT_FOUND,
			`Route not found: ${req.method} ${req.originalUrl}`,
		),
	);
};
