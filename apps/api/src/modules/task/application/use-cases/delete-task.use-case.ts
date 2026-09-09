import { Inject, Injectable, NotFoundException } from '@nestjs/common';
import {
  type ITaskRepository,
  TASK_REPOSITORY,
} from '../../domain/repository/task.repository.interface';
import { S3Service } from '../../../s3/s3.service';

@Injectable()
export class DeleteTaskUseCase {
  constructor(
    @Inject(TASK_REPOSITORY)
    private readonly taskRepo: ITaskRepository,
    private readonly s3Service: S3Service,
  ) {}

  async execute(id: number): Promise<void> {
    const task = await this.taskRepo.findById(id);
    if (!task) {
      throw new NotFoundException(`Task with id ${id} not found`);
    }

    if (task.imgUrl) {
      await this.s3Service.deleteFile(task.imgUrl);
    }

    await this.taskRepo.delete(id);
  }
}
