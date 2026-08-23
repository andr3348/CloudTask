import { Inject, Injectable, NotFoundException } from '@nestjs/common';
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
    const task = await this.taskRepo.findById(id);
    if (!task) {
      throw new NotFoundException(`Task with id ${id} not found`);
    }
    await this.taskRepo.delete(id);
  }
}
