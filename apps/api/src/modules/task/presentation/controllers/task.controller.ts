import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  ParseIntPipe,
  Post,
  Put,
  UploadedFile,
  UseInterceptors,
  BadRequestException,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { GetTaskUseCase } from '../../application/use-cases/get-task.use-case';
import { ListTasksUseCase } from '../../application/use-cases/list-tasks.use-case';
import { CreateTaskUseCase } from '../../application/use-cases/create-task.use-case';
import { UpdateTaskUseCase } from '../../application/use-cases/update-task.use-case';
import { DeleteTaskUseCase } from '../../application/use-cases/delete-task.use-case';
import { CreateTaskDto } from '../dtos/create-task.dto';
import { UpdateTaskDto } from '../dtos/update-task.dto';
import { TaskDto } from '../dtos/task.dto';
import { S3Service } from '../../../s3/s3.service';

@Controller('tasks')
export class TaskController {
  constructor(
    private readonly getTask: GetTaskUseCase,
    private readonly listTasks: ListTasksUseCase,
    private readonly createTask: CreateTaskUseCase,
    private readonly updateTask: UpdateTaskUseCase,
    private readonly deleteTask: DeleteTaskUseCase,
    private readonly s3Service: S3Service,
  ) {}

  @Post('upload')
  @UseInterceptors(
    FileInterceptor('file', {
      limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
    }),
  )
  async uploadImage(
    @UploadedFile() file?: Express.Multer.File,
  ): Promise<{ url: string }> {
    if (!file) {
      throw new BadRequestException('No image file provided');
    }

    if (!file.mimetype.startsWith('image/')) {
      throw new BadRequestException('Only image files are allowed');
    }

    const url = await this.s3Service.uploadFile(file);
    return { url };
  }

  @Get(':id')
  async findById(
    @Param('id', ParseIntPipe) id: number,
  ): Promise<TaskDto | null> {
    const task = await this.getTask.execute(id);
    return task ? TaskDto.fromEntity(task) : null;
  }

  @Get()
  async findAll(): Promise<TaskDto[]> {
    const tasks = await this.listTasks.execute();
    return tasks.map((task) => TaskDto.fromEntity(task));
  }

  @Post()
  async create(@Body() dto: CreateTaskDto): Promise<TaskDto> {
    const task = await this.createTask.execute(dto);
    return TaskDto.fromEntity(task);
  }

  @Put(':id')
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() dto: UpdateTaskDto,
  ): Promise<TaskDto> {
    const task = await this.updateTask.execute(id, dto);
    return TaskDto.fromEntity(task);
  }

  @Delete(':id')
  async delete(@Param('id', ParseIntPipe) id: number): Promise<void> {
    await this.deleteTask.execute(id);
  }
}
