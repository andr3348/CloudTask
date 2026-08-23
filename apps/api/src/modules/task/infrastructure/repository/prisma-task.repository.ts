import { Injectable } from '@nestjs/common';
import {
  CreateTaskInput,
  ITaskRepository,
  UpdateTaskInput,
} from '../../domain/repository/task.repository.interface';
import { PrismaService } from 'src/modules/prisma/prisma.service';
import { TaskEntity } from '../../domain/entity/task.entity';

@Injectable()
export class PrismaTaskRepository implements ITaskRepository {
  constructor(private readonly prisma: PrismaService) {}

  async findById(id: number): Promise<TaskEntity | null> {
    const task = await this.prisma.task.findUnique({
      where: { id },
    });
    return task ? new TaskEntity(task) : null;
  }

  async findAll(): Promise<TaskEntity[]> {
    const tasks = await this.prisma.task.findMany();
    return tasks.map((task) => new TaskEntity(task));
  }

  async create(input: CreateTaskInput): Promise<TaskEntity> {
    const task = await this.prisma.task.create({
      data: {
        title: input.title,
        description: input.description ?? null,
        status: input.status ?? 'PENDING',
        priority: input.priority ?? 'MEDIUM',
        dueDate: input.dueDate ?? null,
      },
    });
    return new TaskEntity(task);
  }

  async update(id: number, input: UpdateTaskInput): Promise<TaskEntity> {
    const task = await this.prisma.task.update({
      where: { id },
      data: {
        title: input.title,
        description: input.description ?? null,
        status: input.status,
        priority: input.priority,
        dueDate: input.dueDate ?? null,
      },
    });
    return new TaskEntity(task);
  }

  async delete(id: number): Promise<void> {
    await this.prisma.task.delete({
      where: { id },
    });
  }
}
