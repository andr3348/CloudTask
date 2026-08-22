import { Inject, Injectable, NotFoundException } from '@nestjs/common';
import {
  type ITaskRepository,
  TASK_REPOSITORY,
} from '../../domain/repository/task.repository.interface';
import { TaskEntity } from '../../domain/entity/task.entity';

@Injectable()
export class GetTaskUseCase {
  constructor(
    @Inject(TASK_REPOSITORY)
    private readonly taskRepo: ITaskRepository,
  ) {}

  async execute(id: number): Promise<TaskEntity | null> {
    const task = await this.taskRepo.findById(id);
    if (!task) throw new NotFoundException(`Task with id ${id} not found`);
    return task;
  }
}
