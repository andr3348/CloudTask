import { Injectable, Logger } from '@nestjs/common';
import {
  S3Client,
  PutObjectCommand,
  DeleteObjectCommand,
} from '@aws-sdk/client-s3';

@Injectable()
export class S3Service {
  private readonly logger = new Logger(S3Service.name);
  private readonly s3Client: S3Client;
  private readonly bucketName: string;
  private readonly region: string;

  constructor() {
    this.region = process.env.AWS_REGION || 'us-east-1';
    this.bucketName = process.env.AWS_S3_BUCKET || 'taskcloud2';

    const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
    const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;

    if (!accessKeyId || !secretAccessKey) {
      this.logger.warn(
        'AWS credentials not fully provided in environment variables',
      );
    }

    this.s3Client = new S3Client({
      region: this.region,
      credentials:
        accessKeyId && secretAccessKey
          ? {
              accessKeyId,
              secretAccessKey,
            }
          : undefined,
    });
  }

  async uploadFile(
    file: Express.Multer.File,
    folder = 'tasks',
  ): Promise<string> {
    const cleanFileName = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
    const key = `${folder}/${Date.now()}-${cleanFileName}`;

    await this.s3Client.send(
      new PutObjectCommand({
        Bucket: this.bucketName,
        Key: key,
        Body: file.buffer,
        ContentType: file.mimetype,
      }),
    );

    const publicUrl = `https://${this.bucketName}.s3.${this.region}.amazonaws.com/${key}`;
    this.logger.log(`Uploaded file to S3: ${publicUrl}`);
    return publicUrl;
  }

  async deleteFile(fileUrl: string): Promise<void> {
    const key = this.extractKeyFromUrl(fileUrl);
    if (!key) {
      this.logger.warn(`Could not extract S3 key from URL: ${fileUrl}`);
      return;
    }

    try {
      await this.s3Client.send(
        new DeleteObjectCommand({
          Bucket: this.bucketName,
          Key: key,
        }),
      );
      this.logger.log(`Deleted S3 object with key: ${key}`);
    } catch (error) {
      this.logger.error(
        `Failed to delete S3 object: ${key}`,
        error instanceof Error ? error.stack : error,
      );
    }
  }

  private extractKeyFromUrl(fileUrl: string): string | null {
    try {
      const url = new URL(fileUrl);
      // Handles https://<bucket>.s3.<region>.amazonaws.com/<key>
      // pathname starts with '/' so remove leading slash
      const key = decodeURIComponent(url.pathname.replace(/^\/+/, ''));
      return key || null;
    } catch {
      return null;
    }
  }
}
