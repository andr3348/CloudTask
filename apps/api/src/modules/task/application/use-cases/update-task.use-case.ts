import { Inject, Injectable, NotFoundException } from '@nestjs/common';
import {
  type ITaskRepository,
  TASK_REPOSITORY,
  UpdateTaskInput,
} from '../../domain/repository/task.repository.interface';
import { TaskEntity } from '../../domain/entity/task.entity';
import { S3Service } from '../../../s3/s3.service';

@Injectable()
export class UpdateTaskUseCase {
  constructor(
    @Inject(TASK_REPOSITORY)
    private readonly taskRepo: ITaskRepository,
    private readonly s3Service: S3Service,
  ) {}

  async execute(id: number, input: UpdateTaskInput): Promise<TaskEntity> {
    const task = await this.taskRepo.findById(id);
    if (!task) {
      throw new NotFoundException(`Task with id ${id} not found`);
    }

    // If the image is being changed or removed, delete the old image from S3
    if (task.imgUrl && input.imgUrl !== undefined && task.imgUrl !== input.imgUrl) {
      await this.s3Service.deleteFile(task.imgUrl);
    }

    return await this.taskRepo.update(id, input);
  }
}
