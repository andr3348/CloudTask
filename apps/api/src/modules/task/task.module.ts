import { Module } from '@nestjs/common';
import { PrismaModule } from '../prisma/prisma.module';
import { TaskController } from './presentation/controllers/task.controller';
import { ListTasksUseCase } from './application/use-cases/list-tasks.use-case';
import { GetTaskUseCase } from './application/use-cases/get-task.use-case';
import { CreateTaskUseCase } from './application/use-cases/create-task.use-case';
import { UpdateTaskUseCase } from './application/use-cases/update-task.use-case';
import { DeleteTaskUseCase } from './application/use-cases/delete-task.use-case';
import { TASK_REPOSITORY } from './domain/repository/task.repository.interface';
import { PrismaTaskRepository } from './infrastructure/repository/prisma-task.repository';

@Module({
  imports: [PrismaModule],
  controllers: [TaskController],
  providers: [
    ListTasksUseCase,
    GetTaskUseCase,
    CreateTaskUseCase,
    UpdateTaskUseCase,
    DeleteTaskUseCase,
    { provide: TASK_REPOSITORY, useClass: PrismaTaskRepository },
  ],
  exports: [],
})
export class TaskModule {}
