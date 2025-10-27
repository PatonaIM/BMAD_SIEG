# Coding Standards

## Overview
This document defines the coding standards and best practices for the Teamified projects, covering both backend (NestJS) and frontend (React) development.

## Backend Standards (NestJS)

### Code Organization

#### Module Structure
```
src/
├── {feature}/
│   ├── entities/
│   │   ├── {feature}.entity.ts
│   │   └── {feature}.entity.spec.ts
│   ├── services/
│   │   ├── {feature}.service.ts
│   │   └── {feature}.service.spec.ts
│   ├── controllers/
│   │   ├── {feature}.controller.ts
│   │   └── {feature}.controller.spec.ts
│   ├── dto/
│   │   ├── {feature}.dto.ts
│   │   └── {feature}.dto.spec.ts
│   └── {feature}.module.ts
```

#### File Naming Conventions
- **Entities**: `{feature}.entity.ts` (e.g., `eor-profile.entity.ts`)
- **Services**: `{feature}.service.ts` (e.g., `profile-completion.service.ts`)
- **Controllers**: `{feature}.controller.ts` (e.g., `auth.controller.ts`)
- **DTOs**: `{feature}.dto.ts` (e.g., `login-credentials.dto.ts`)
- **Tests**: `{feature}.spec.ts` (e.g., `eor-profile.entity.spec.ts`)

### Entity Standards

#### TypeORM Decorators
```typescript
@Entity('table_name')
export class EntityName {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ name: 'column_name', type: 'varchar', length: 100, nullable: true })
  columnName: string | null;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;
}
```

#### Validation Decorators
```typescript
import {
  IsOptional,
  IsString,
  MaxLength,
  IsDateString,
  IsPhoneNumber,
  IsArray,
  IsIn,
  IsInt,
  Min,
  Max,
  IsBoolean,
  Length,
  ValidateNested,
} from 'class-validator';

export class EntityName {
  @IsOptional()
  @IsString()
  @MaxLength(100)
  @Column({ name: 'field_name', nullable: true })
  fieldName: string | null;
}
```

#### Relationships
```typescript
// One-to-One
@OneToOne(() => RelatedEntity)
@JoinColumn({ name: 'related_id' })
related: RelatedEntity;

// One-to-Many
@OneToMany(() => RelatedEntity, (related) => related.parent)
related: RelatedEntity[];

// Many-to-One
@ManyToOne(() => ParentEntity)
@JoinColumn({ name: 'parent_id' })
parent: ParentEntity;
```

### Service Standards

#### Service Structure
```typescript
@Injectable()
export class FeatureService {
  constructor(
    private readonly repository: Repository<FeatureEntity>,
    private readonly logger: Logger,
  ) {}

  async create(data: CreateFeatureDto): Promise<FeatureEntity> {
    try {
      const entity = this.repository.create(data);
      return await this.repository.save(entity);
    } catch (error) {
      this.logger.error(`Failed to create feature: ${error.message}`);
      throw new InternalServerErrorException('Failed to create feature');
    }
  }
}
```

#### Error Handling
```typescript
// Use NestJS built-in exceptions
import {
  BadRequestException,
  NotFoundException,
  InternalServerErrorException,
  UnauthorizedException,
} from '@nestjs/common';

// Custom error handling
if (!entity) {
  throw new NotFoundException(`Feature with ID ${id} not found`);
}

if (!isAuthorized) {
  throw new UnauthorizedException('Insufficient permissions');
}
```

### Controller Standards

#### Controller Structure
```typescript
@Controller('api/v1/features')
@UseGuards(JwtAuthGuard)
export class FeatureController {
  constructor(private readonly featureService: FeatureService) {}

  @Post()
  @UsePipes(new ValidationPipe({ whitelist: true }))
  async create(@Body() createFeatureDto: CreateFeatureDto): Promise<FeatureEntity> {
    return this.featureService.create(createFeatureDto);
  }

  @Get(':id')
  async findOne(@Param('id') id: string): Promise<FeatureEntity> {
    return this.featureService.findOne(id);
  }
}
```

#### HTTP Status Codes
- `200` - Success (GET, PUT, PATCH)
- `201` - Created (POST)
- `204` - No Content (DELETE)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

### DTO Standards

#### Request DTOs
```typescript
export class CreateFeatureDto {
  @IsString()
  @MaxLength(100)
  @ApiProperty({ description: 'Feature name', maxLength: 100 })
  name: string;

  @IsOptional()
  @IsString()
  @MaxLength(500)
  @ApiProperty({ description: 'Feature description', required: false })
  description?: string;
}
```

#### Response DTOs
```typescript
export class FeatureResponseDto {
  @ApiProperty()
  id: string;

  @ApiProperty()
  name: string;

  @ApiProperty()
  description: string;

  @ApiProperty()
  createdAt: Date;

  @ApiProperty()
  updatedAt: Date;
}
```

## Frontend Standards (React + TypeScript)

### Component Structure

#### Functional Components
```typescript
import React, { useState, useEffect } from 'react';
import type { ComponentProps } from './types';

interface ComponentProps {
  title: string;
  onSave: (data: FormData) => void;
  isLoading?: boolean;
}

const ComponentName: React.FC<ComponentProps> = ({ 
  title, 
  onSave, 
  isLoading = false 
}) => {
  const [formData, setFormData] = useState<FormData>({
    // initial state
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="component-name">
      <h2>{title}</h2>
      <form onSubmit={handleSubmit}>
        {/* form content */}
      </form>
    </div>
  );
};

export default ComponentName;
```

#### File Organization
```
src/
├── components/
│   ├── {ComponentName}/
│   │   ├── index.ts
│   │   ├── {ComponentName}.tsx
│   │   ├── {ComponentName}.test.tsx
│   │   └── {ComponentName}.module.css (if using CSS modules)
│   └── {ComponentName}.tsx (for simple components)
├── pages/
│   ├── {PageName}/
│   │   ├── index.ts
│   │   ├── {PageName}.tsx
│   │   └── {PageName}.test.tsx
│   └── {PageName}.tsx
├── services/
│   ├── {serviceName}.ts
│   └── {serviceName}.test.ts
├── types/
│   └── {feature}.types.ts
└── utils/
    └── {utilityName}.ts
```

### State Management

#### Local State
```typescript
const [formData, setFormData] = useState<FormData>({
  email: '',
  password: '',
});

const [errors, setErrors] = useState<{ [key: string]: string }>({});
const [isLoading, setIsLoading] = useState(false);
```

#### Form Handling
```typescript
const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const { name, value, type, checked } = e.target;
  setFormData(prev => ({
    ...prev,
    [name]: type === 'checkbox' ? checked : value,
  }));
  
  // Clear error when user starts typing
  if (errors[name]) {
    setErrors(prev => ({ ...prev, [name]: '' }));
  }
};
```

### Validation

#### Client-Side Validation
```typescript
const validateEmail = (email: string): string => {
  if (!email) return 'Email is required';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) return 'Please enter a valid email address';
  return '';
};

const validateForm = (): boolean => {
  const newErrors: { [key: string]: string } = {};
  
  const emailError = validateEmail(formData.email);
  if (emailError) newErrors.email = emailError;
  
  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
```

### Error Handling

#### Error Display
```typescript
{errors.general && (
  <div className="form-error form-error--general">
    {errors.general}
  </div>
)}

{errors.email && (
  <div id="email-error" className="form-error" role="alert">
    {errors.email}
  </div>
)}
```

#### API Error Handling
```typescript
try {
  const result = await apiCall(data);
  // handle success
} catch (error) {
  if (error instanceof Error) {
    setErrors({ general: error.message });
  } else {
    setErrors({ general: 'An unexpected error occurred' });
  }
} finally {
  setIsLoading(false);
}
```

## Testing Standards

### Backend Testing (Jest)

#### Test Structure
```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { FeatureService } from './feature.service';

describe('FeatureService', () => {
  let service: FeatureService;
  let mockRepository: jest.Mocked<Repository<FeatureEntity>>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FeatureService,
        {
          provide: getRepositoryToken(FeatureEntity),
          useValue: {
            find: jest.fn(),
            findOne: jest.fn(),
            save: jest.fn(),
            create: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<FeatureService>(FeatureService);
    mockRepository = module.get(getRepositoryToken(FeatureEntity));
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('findOne', () => {
    it('should return a feature when found', async () => {
      const mockFeature = new FeatureEntity();
      mockRepository.findOne.mockResolvedValue(mockFeature);

      const result = await service.findOne('test-id');
      
      expect(result).toBe(mockFeature);
      expect(mockRepository.findOne).toHaveBeenCalledWith({ where: { id: 'test-id' } });
    });

    it('should throw NotFoundException when feature not found', async () => {
      mockRepository.findOne.mockResolvedValue(null);

      await expect(service.findOne('test-id')).rejects.toThrow(NotFoundException);
    });
  });
});
```

### Frontend Testing (Vitest + React Testing Library)

#### Test Structure
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ComponentName from './ComponentName';

describe('ComponentName', () => {
  const mockProps = {
    title: 'Test Title',
    onSave: vi.fn(),
  };

  it('renders with title', () => {
    render(<ComponentName {...mockProps} />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('calls onSave when form is submitted', async () => {
    render(<ComponentName {...mockProps} />);
    
    const submitButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockProps.onSave).toHaveBeenCalled();
    });
  });
});
```

## Code Quality Standards

### ESLint Configuration
- Use TypeScript ESLint rules
- Enforce consistent code style
- Catch common programming errors
- Maintain code quality standards

### Prettier Configuration
- Consistent code formatting
- Automatic code formatting on save
- Unified code style across the team

### TypeScript Configuration
- Strict mode enabled
- No implicit any types
- Strict null checks
- Proper type definitions

## Performance Standards

### Backend
- Use database indexes for frequently queried fields
- Implement caching strategies where appropriate
- Use pagination for large result sets
- Optimize database queries

### Frontend
- Lazy load components when possible
- Implement proper memoization
- Use React.memo for expensive components
- Optimize bundle size

## Security Standards

### Backend
- Input validation and sanitization
- JWT token validation
- Role-based access control
- SQL injection prevention
- XSS protection

### Frontend
- Input validation
- Secure storage of sensitive data
- HTTPS enforcement
- Content Security Policy

## Documentation Standards

### Code Comments
```typescript
/**
 * Creates a new feature in the system
 * @param data - The feature data to create
 * @returns Promise<FeatureEntity> - The created feature
 * @throws BadRequestException - If validation fails
 * @throws InternalServerErrorException - If database operation fails
 */
async create(data: CreateFeatureDto): Promise<FeatureEntity> {
  // implementation
}
```

### API Documentation
- Use Swagger/OpenAPI decorators
- Document all endpoints
- Include request/response examples
- Document error responses

### README Files
- Project setup instructions
- Development workflow
- Testing instructions
- Deployment guide

---

**Last Updated**: 2025-08-29  
**Version**: 1.0  
**Author**: James (Full Stack Developer)
