import { Inject, Injectable } from '@nestjs/common';
import {
  CreateTaskInput,
  type ITaskRepository,
  TASK_REPOSITORY,
} from '../../domain/repository/task.repository.interface';
import { TaskEntity } from '../../domain/entity/task.entity';

@Injectable()
export class CreateTaskUseCase {
  constructor(
    @Inject(TASK_REPOSITORY)
    private readonly taskRepo: ITaskRepository,
  ) {}

  async execute(input: CreateTaskInput): Promise<TaskEntity> {
    return await this.taskRepo.create(input);
  }
}
