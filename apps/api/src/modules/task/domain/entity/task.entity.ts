export interface TaskEntityProps {
  id: number;
  title: string;
  description: string | null;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  dueDate: Date | null;
  createdAt: Date;
  updatedAt: Date;
}

export class TaskEntity {
  constructor(private readonly props: TaskEntityProps) {}

  get id(): number {
    return this.props.id;
  }

  get title(): string {
    return this.props.title;
  }

  get description(): string | null {
    return this.props.description;
  }

  get status(): 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' {
    return this.props.status;
  }

  get priority(): 'LOW' | 'MEDIUM' | 'HIGH' {
    return this.props.priority;
  }

  get dueDate(): Date | null {
    return this.props.dueDate;
  }

  get createdAt(): Date {
    return this.props.createdAt;
  }

  get updatedAt(): Date {
    return this.props.updatedAt;
  }
}
