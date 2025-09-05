# TestSpecAI Project Rules and Guidelines

## 📋 Overview

This directory contains comprehensive rules and guidelines for implementing the TestSpecAI project. These rules ensure consistency, quality, and proper implementation across all development tasks.

## 📁 File Structure

```
.cursor/rules/
├── README.md                           # This file - how to use the rules
├── project_structure.mdc               # Main project structure and architecture
├── backend_implementation.mdc          # Backend (FastAPI) implementation guidelines
├── frontend_implementation.mdc         # Frontend (React) implementation guidelines
├── ai_services_implementation.mdc      # AI services (NLP + LLM) implementation
├── document_processing.mdc             # Document processing implementation
└── quality_assurance.mdc               # Testing and quality assurance guidelines
```

## 🎯 How to Use These Rules

### **Before Starting Any Task:**

1. **Read the relevant rule file** for your task type:
   - **Backend tasks** → `backend_implementation.mdc`
   - **Frontend tasks** → `frontend_implementation.mdc`
   - **AI services** → `ai_services_implementation.mdc`
   - **Document processing** → `document_processing.mdc`
   - **All tasks** → `project_structure.mdc` (mandatory)

2. **Check the implementation checklist** at the bottom of each rule file

3. **Follow the exact patterns** and code examples provided

4. **Use the quality assurance checklist** before marking tasks complete

### **During Implementation:**

- **Follow the exact folder structure** specified in `project_structure.mdc`
- **Use the provided code patterns** as templates
- **Implement proper error handling** as shown in examples
- **Add comprehensive tests** following the testing guidelines
- **Follow naming conventions** and coding standards

### **Before Marking Tasks Complete:**

- **Run all quality assurance checks** from `quality_assurance.mdc`
- **Verify code coverage** meets requirements
- **Test all functionality** thoroughly
- **Update documentation** if needed

## 🔧 Rule Categories

### **1. Project Structure (`project_structure.mdc`)**
- **Technology stack** (finalized, no changes allowed)
- **Folder structure** (mandatory layout)
- **Data models** (exact specifications)
- **API design** (RESTful conventions)
- **Implementation checklist** (step-by-step verification)

### **2. Backend Implementation (`backend_implementation.mdc`)**
- **FastAPI application** setup and configuration
- **SQLAlchemy models** with proper relationships
- **Pydantic schemas** for validation
- **CRUD operations** patterns
- **API endpoints** implementation
- **Error handling** and logging
- **Database migrations** with Alembic

### **3. Frontend Implementation (`frontend_implementation.mdc`)**
- **React application** setup with TypeScript
- **Zustand state management** patterns
- **API services** integration
- **Custom React hooks** implementation
- **Component patterns** and best practices
- **Styling guidelines** with Ant Design
- **Testing strategies** for components

### **4. AI Services (`ai_services_implementation.mdc`)**
- **NLP service** for test matching
- **Local LLM service** for test generation
- **Vector embeddings** with pgvector
- **Prompt engineering** templates
- **Background processing** for AI operations
- **Security and performance** considerations

### **5. Document Processing (`document_processing.mdc`)**
- **Multi-format support** (Word, PDF, Excel)
- **Text extraction** algorithms
- **Requirement pattern** recognition
- **File upload** and validation
- **Background processing** for large files
- **Error handling** for corrupted files

### **6. Quality Assurance (`quality_assurance.mdc`)**
- **Testing strategy** and coverage requirements
- **Unit testing** patterns for backend and frontend
- **Integration testing** approaches
- **Performance testing** guidelines
- **Security testing** checklist
- **Code quality** standards

## ⚠️ Critical Rules (Never Break)

### **Technology Stack (FINAL)**
- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic v2
- **Frontend**: React 18+ + TypeScript + Zustand + Ant Design Pro
- **Database**: SQLite (dev) + PostgreSQL + pgvector (prod)
- **AI**: Local LLM only (no external APIs)
- **No Docker, No CI/CD, No Authentication**

### **Data Models (EXACT)**
- **TestSpecification**: `requirementIds` (array), `testSteps` with GenericCommand references
- **TestStep**: `action` and `expectedResult` are GenericCommand references only
- **Parameter**: `categoryId` references user-defined categories
- **GenericCommand**: `categoryId` references user-defined categories
- **Categories**: User-defined, not predefined enums

### **API Design (MANDATORY)**
- **Base URL**: `/api/v1`
- **RESTful conventions** for all endpoints
- **Proper error handling** with structured responses
- **Async/await** for all database operations
- **Pydantic validation** for all requests/responses

## 🚀 Quick Start Guide

### **For Backend Tasks:**
1. Read `project_structure.mdc` (sections 1-3)
2. Read `backend_implementation.mdc` (full file)
3. Follow the exact folder structure
4. Use the provided code patterns
5. Implement comprehensive tests
6. Run quality assurance checks

### **For Frontend Tasks:**
1. Read `project_structure.mdc` (sections 1-3)
2. Read `frontend_implementation.mdc` (full file)
3. Follow the component patterns
4. Use Zustand for state management
5. Implement proper TypeScript types
6. Add component tests

### **For AI Service Tasks:**
1. Read `project_structure.mdc` (sections 1-3)
2. Read `ai_services_implementation.mdc` (full file)
3. Set up local LLM infrastructure
4. Implement proper error handling
5. Add comprehensive tests
6. Verify security measures

## 📊 Quality Metrics

### **Code Coverage Requirements:**
- **Backend**: Minimum 80%
- **Frontend**: Minimum 70%
- **Critical paths**: 100% (AI services, document processing)

### **Performance Requirements:**
- **API response time**: < 200ms for simple operations
- **AI processing**: < 30 seconds for test generation
- **Document processing**: < 60 seconds for 10MB files
- **Concurrent users**: Support 20-30 users

### **Security Requirements:**
- **Input validation**: All user inputs validated
- **Error handling**: No sensitive data in error messages
- **File upload**: Comprehensive validation and sanitization
- **Rate limiting**: Prevent abuse of AI services

## 🔍 Troubleshooting

### **Common Issues:**

1. **"Folder structure doesn't match"**
   - Check `project_structure.mdc` for exact layout
   - Ensure all required directories exist

2. **"Database model relationships wrong"**
   - Follow the exact model specifications in `project_structure.mdc`
   - Use the provided relationship patterns

3. **"API endpoint not working"**
   - Check `backend_implementation.mdc` for endpoint patterns
   - Ensure proper error handling is implemented

4. **"Frontend component not rendering"**
   - Check `frontend_implementation.mdc` for component patterns
   - Ensure proper TypeScript types are defined

5. **"AI service failing"**
   - Check `ai_services_implementation.mdc` for setup requirements
   - Verify local LLM server is running

### **Getting Help:**

1. **Check the relevant rule file** first
2. **Look at the code examples** provided
3. **Verify your implementation** against the checklists
4. **Run the quality assurance checks**
5. **Check the PRD** (`.taskmaster/docs/prd.txt`) for business requirements

## 📝 Maintenance

### **Updating Rules:**
- Rules should be updated when new patterns emerge
- All team members should be notified of rule changes
- Examples should be kept synchronized with actual code
- Deprecated patterns should be clearly marked

### **Rule Quality:**
- Rules should be actionable and specific
- Examples should come from actual code
- References should be kept up to date
- Patterns should be consistently enforced

---

**Remember**: These rules are the single source of truth for TestSpecAI implementation. Always refer to them before starting any task and follow them exactly to ensure project success.
