import prisma from '@/config/prisma';

export const getAllUsers = async () => {
	return prisma.user.findMany({
		select: {
			id: true,
			email: true,
			name: true,
			createdAt: true,
			updatedAt: true,
		},
	});
};

export const createUser = async (data: { email: string; name?: string }) => {
	return prisma.user.create({
		data,
	});
};
