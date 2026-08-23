import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  ParseIntPipe,
  Patch,
  Post,
  Put,
} from '@nestjs/common';
import { GetTaskUseCase } from '../../application/use-cases/get-task.use-case';
import { ListTasksUseCase } from '../../application/use-cases/list-tasks.use-case';
import { CreateTaskUseCase } from '../../application/use-cases/create-task.use-case';
import { UpdateTaskUseCase } from '../../application/use-cases/update-task.use-case';
import { DeleteTaskUseCase } from '../../application/use-cases/delete-task.use-case';
import { CreateTaskDto } from '../dtos/create-task.dto';
import { TaskEntity } from '../../domain/entity/task.entity';
import { UpdateTaskDto } from '../dtos/update-task.dto';

@Controller('tasks')
export class TaskController {
  constructor(
    private readonly getTask: GetTaskUseCase,
    private readonly listTasks: ListTasksUseCase,
    private readonly createTask: CreateTaskUseCase,
    private readonly updateTask: UpdateTaskUseCase,
    private readonly deleteTask: DeleteTaskUseCase,
  ) {}

  @Get(':id')
  async findById(
    @Param('id', ParseIntPipe) id: number,
  ): Promise<TaskEntity | null> {
    const task = await this.getTask.execute(id);
    return task;
  }

  @Get()
  async findAll(): Promise<TaskEntity[]> {
    const tasks = await this.listTasks.execute();
    return tasks;
  }

  @Post()
  async create(@Body() dto: CreateTaskDto): Promise<TaskEntity> {
    const task = await this.createTask.execute(dto);
    return task;
  }

  @Put(':id')
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() dto: UpdateTaskDto,
  ): Promise<TaskEntity> {
    const task = await this.updateTask.execute(id, dto);
    return task;
  }

  @Delete(':id')
  async delete(@Param('id', ParseIntPipe) id: number): Promise<void> {
    await this.deleteTask.execute(id);
  }
}
