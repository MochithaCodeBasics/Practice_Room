import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ModulesService } from './modules.service.js';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard.js';
import { AdminGuard } from '../common/guards/admin.guard.js';
import { CreateModuleDto, UpdateModuleDto } from './dto/create-module.dto.js';

@Controller('api/modules')
export class ModulesController {
  constructor(private readonly modulesService: ModulesService) { }

  @Get()
  async findAll() {
    return this.modulesService.findAll();
  }

  @Get(':slug/questions')
  async findQuestions(
    @Param('slug') slug: string,
    @Query('difficulty') difficulty?: string,
    @Query('topic') topic?: string,
    @Query('search') search?: string,
  ) {
    return this.modulesService.findQuestionsBySlug(slug, {
      difficulty,
      topic,
      search,
    });
  }

  @Get(':slug/questions/:questionSlug')
  async findOneQuestion(
    @Param('slug') slug: string,
    @Param('questionSlug') questionSlug: string,
  ) {
    return this.modulesService.findQuestionBySlug(slug, questionSlug);
  }

  @Post()
  @UseGuards(JwtAuthGuard, AdminGuard)
  @HttpCode(HttpStatus.CREATED)
  async create(@Body() dto: CreateModuleDto) {
    return this.modulesService.create(dto);
  }

  @Patch(':moduleId')
  @UseGuards(JwtAuthGuard, AdminGuard)
  async update(
    @Param('moduleId') moduleId: string,
    @Body() dto: UpdateModuleDto,
  ) {
    return this.modulesService.update(moduleId, dto);
  }

  @Delete(':moduleId')
  @UseGuards(JwtAuthGuard, AdminGuard)
  @HttpCode(HttpStatus.NO_CONTENT)
  async remove(@Param('moduleId') moduleId: string) {
    await this.modulesService.remove(moduleId);
  }
}
