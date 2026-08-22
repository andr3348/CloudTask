import { Inject, Injectable } from '@nestjs/common';
import {
  type ITaskRepository,
  TASK_REPOSITORY,
} from '../../domain/repository/task.repository.interface';

@Injectable()
export class DeleteTaskUseCase {
  constructor(
    @Inject(TASK_REPOSITORY)
    private readonly taskRepo: ITaskRepository,
  ) {}

  async execute(id: number): Promise<void> {
    await this.taskRepo.findById(id); // throws NotFoundException (404) if task not found
    await this.taskRepo.delete(id);
  }
}
