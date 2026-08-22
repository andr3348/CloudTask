import { Inject, Injectable } from '@nestjs/common';
import {
  type ITaskRepository,
  TASK_REPOSITORY,
} from '../../domain/repository/task.repository.interface';
import { TaskEntity } from '../../domain/entity/task.entity';

@Injectable()
export class ListTasksUseCase {
  constructor(
    @Inject(TASK_REPOSITORY)
    private readonly taskRepo: ITaskRepository,
  ) {}

  async execute(): Promise<TaskEntity[]> {
    return await this.taskRepo.findAll();
  }
}
