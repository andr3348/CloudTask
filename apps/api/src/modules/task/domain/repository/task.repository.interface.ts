import { TaskEntity } from '../entity/task.entity';

export type TaskStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH';

export interface CreateTaskInput {
  title: string;
  description?: string | null;
  status?: TaskStatus | null;
  priority?: TaskPriority | null;
  dueDate?: Date | null;
}

export interface UpdateTaskInput {
  title: string;
  description?: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  dueDate?: Date | null;
}

export interface ITaskRepository {
  findById(id: number): Promise<TaskEntity | null>;
  findAll(): Promise<TaskEntity[]>;
  create(input: CreateTaskInput): Promise<TaskEntity>;
  update(id: number, input: UpdateTaskInput): Promise<TaskEntity>;
  delete(id: number): Promise<void>;
}

export const TASK_REPOSITORY = Symbol('ITaskRepository');
