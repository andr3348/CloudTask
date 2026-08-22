import { Injectable, OnModuleDestroy, OnModuleInit } from "@nestjs/common";
import { PrismaPgClient } from '@cloudtask/db';

@Injectable()
export class PrismaService extends PrismaPgClient implements OnModuleInit, OnModuleDestroy {
    async onModuleInit() {
        await this.$connect();
    }

    async onModuleDestroy() {
        await this.$disconnect();
    }
}