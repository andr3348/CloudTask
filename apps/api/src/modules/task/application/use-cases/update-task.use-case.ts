import { Inject, Injectable } from '@nestjs/common';
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
    await this.taskRepo.findById(id); // throws NotFoundException (404) if task not found
    return await this.taskRepo.update(id, input);
  }
}
