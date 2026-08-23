import {
  IsDate,
  IsIn,
  IsNotEmpty,
  IsOptional,
  IsString,
  Length,
} from 'class-validator';
import { Type } from 'class-transformer';
import {
  type TaskPriority,
  type TaskStatus,
} from '../../domain/repository/task.repository.interface';

const TASK_STATUSES: TaskStatus[] = ['PENDING', 'IN_PROGRESS', 'COMPLETED'];
const TASK_PRIORITIES: TaskPriority[] = ['LOW', 'MEDIUM', 'HIGH'];

export class UpdateTaskDto {
  @IsString()
  @IsNotEmpty({ message: 'Title is required' })
  title: string;

  @IsOptional()
  @IsString()
  @Length(0, 500, { message: 'Description must be at most 500 characters' })
  description?: string;

  @IsIn(TASK_STATUSES)
  status: TaskStatus;

  @IsIn(TASK_PRIORITIES)
  priority: TaskPriority;

  @IsOptional()
  @Type(() => Date)
  @IsDate()
  dueDate?: Date;
}
