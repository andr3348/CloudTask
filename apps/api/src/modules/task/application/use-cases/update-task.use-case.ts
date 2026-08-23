import { Inject, Injectable, NotFoundException } from '@nestjs/common';
import {
  type ITaskRepository,
  TASK_REPOSITORY,
  UpdateTaskInput,
} from '../../domain/repository/task.repository.interface';
import { TaskEntity } from '../../domain/entity/task.entity';

@Injectable()
export class UpdateTaskUseCase {
  constructor(
    @Inject(TASK_REPOSITORY)
    private readonly taskRepo: ITaskRepository,
  ) {}

  async execute(id: number, input: UpdateTaskInput): Promise<TaskEntity> {
    const task = await this.taskRepo.findById(id);
    if (!task) {
      throw new NotFoundException(`Task with id ${id} not found`);
    }
    return await this.taskRepo.update(id, input);
  }
}
