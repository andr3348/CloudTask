import { TaskEntity } from '../entity/task.entity';

export interface CreateTaskInput {
  title: string;
  description?: string | null;
  status?: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | null;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH' | null;
  dueDate?: Date | null;
}

export interface UpdateTaskInput {
  title: string;
  description?: string | null;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
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
