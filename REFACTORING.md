# Knowledge Graph Research - Refactored Architecture

## 📋 Tổng quan

Hệ thống trích xuất và trực quan hóa Knowledge Graph từ văn bản tiếng Việt, đã được refactor theo các design patterns và best practices.

## 🏗️ Kiến trúc mới

### Cấu trúc thư mục

```
kg-research/
├── src/
│   ├── core/
│   │   └── config.py              # Configuration & Settings
│   ├── data/
│   │   └── generic_models.py      # Pydantic models (Node, Edge, Graph)
│   ├── interfaces/
│   │   ├── base_extractor.py      # Abstract Base Class cho extractors
│   │   └── graph_repository.py    # Repository interface
│   ├── repositories/
│   │   └── json_graph_repository.py  # JSON persistence implementation
│   ├── services/
│   │   ├── text_extractor.py      # Text extraction với LLM
│   │   ├── url_extractor.py       # URL/web crawling
│   │   ├── file_extractor.py      # File-based extraction
│   │   ├── graph_query_service.py # Graph querying operations
│   │   └── graph_visualization_service.py  # HTML visualization
│   └── utils/
│       └── logging_config.py      # Logging setup
├── extract.py                      # CLI for extraction
├── visualize.py                    # CLI for visualization
└── data/
    ├── extracted/                  # Extracted graphs & texts
    ├── merged/                     # Merged graphs
    ├── urls/                       # URL lists
    └── visualizations/             # Generated HTML files
```

## 🎯 Design Patterns được áp dụng

### 1. **Repository Pattern**
- `GraphRepository` interface định nghĩa contract
- `JsonGraphRepository` implement cho JSON persistence
- Dễ dàng mở rộng cho database, XML, GraphML, etc.

### 2. **Strategy Pattern**
- `BaseExtractor` abstract base class
- Concrete implementations: `TextExtractor`, `URLExtractor`, `FileExtractor`
- Dễ dàng thêm extractors mới (PDF, DOCX, API, etc.)

### 3. **Dependency Injection**
- Không còn global singletons
- Dependencies được inject qua constructors
- Dễ test và maintain

### 4. **Separation of Concerns**
- **Models**: Chỉ chứa data structures
- **Services**: Business logic
- **Repositories**: Data persistence
- **CLI**: User interface layer

### 5. **Single Responsibility Principle**
- Mỗi class có một nhiệm vụ rõ ràng
- `GraphVisualizationService`: Chỉ lo visualization
- `GraphQueryService`: Chỉ lo querying
- `JsonGraphRepository`: Chỉ lo load/save

## 🚀 Sử dụng

### Trích xuất từ text

```bash
python3 extract.py --text "Your Vietnamese text here"
```

### Trích xuất từ URL

```bash
python3 extract.py --url https://example.com --output_dir data/extracted
```

### Trích xuất từ danh sách URLs

```bash
python3 extract.py --url_list_file data/urls/hue.txt --output_dir data/extracted
```

### Merge các graphs

```bash
python3 extract.py --merge --output_dir data/extracted --merge_output data/merged/merged_graphs.json
```

### Trực quan hóa

```bash
python3 visualize.py --json_path data/merged/merged_graphs.json --output_path data/visualizations/graph.html
```

### Options nâng cao

```bash
# Logging level
python3 extract.py --url https://example.com --log_level DEBUG

# Disable physics trong visualization
python3 visualize.py --json_path data/merged/merged_graphs.json --no_physics

# Custom dimensions
python3 visualize.py --json_path data/merged/merged_graphs.json --height 1000px --width 100%
```

## 📦 Dependencies

```
python-dotenv
pydantic
openai
requests
bs4
networkx
pyvis
```

## ⚙️ Configuration

Tạo file `.env`:

```env
OPENAI_API_KEY=your_api_key_here
LLM_MODEL_NAME_ANALYSIS=gpt-4o-mini
```

## 🔧 Customization

### Thêm extractor mới

```python
from src.interfaces.base_extractor import BaseExtractor
from src.data.generic_models import GenericGraph

class PDFExtractor(BaseExtractor):
    def validate_source(self, source: str) -> bool:
        return source.endswith('.pdf')
    
    def extract(self, source: str, context=None) -> GenericGraph:
        # Your PDF extraction logic
        pass
```

### Thêm repository mới

```python
from src.interfaces.graph_repository import GraphRepository
from src.data.generic_models import GenericGraph

class Neo4jRepository(GraphRepository):
    def save(self, graph: GenericGraph, path: str) -> bool:
        # Save to Neo4j
        pass
    
    def load(self, path: str) -> GenericGraph:
        # Load from Neo4j
        pass
```

## 🎨 Improvements vs Old Code

### Before (Old)
❌ God Object: `GenericGraphService` (669 lines)  
❌ Global singletons: `text_to_graph_extractor`, `generic_graph_service`  
❌ Mixed concerns: visualization + data management + querying  
❌ Hardcoded values  
❌ Print statements everywhere  
❌ No abstraction/interfaces  

### After (New)
✅ Single Responsibility: Each class has one job  
✅ Dependency Injection: Clean dependencies  
✅ Separated Services: Query, Visualization, Extraction  
✅ Configuration Management: `AppSettings` class  
✅ Proper Logging: Structured logging with levels  
✅ Abstract Interfaces: Easy to extend  
✅ Repository Pattern: Clean data access  
✅ Strategy Pattern: Pluggable extractors  

## 📊 Testing

```bash
# Test extraction
python3 extract.py --text "Huế là cố đô của Việt Nam" --log_level DEBUG

# Test URL extraction
python3 extract.py --url https://vi.wikipedia.org/wiki/Huế

# Test visualization
python3 visualize.py --json_path data/merged/merged_graphs.json --log_level INFO
```

## 🔮 Future Enhancements

1. **Add unit tests** với pytest
2. **Async operations** cho multiple URL crawling
3. **Database support** (Neo4j, PostgreSQL)
4. **Export formats** (GraphML, Cypher, RDF)
5. **Graph algorithms** (centrality, clustering, path finding)
6. **REST API** với FastAPI
7. **Caching layer** cho API calls
8. **Batch processing** với queues

## 📝 Notes

- Old files được rename thành `.old` để backup
- Logging output có thể được saved to file
- Configuration có thể extend cho multiple environments
- Services có thể được wrapped thành microservices

## 🤝 Contributing

Khi thêm features mới:
1. Follow existing patterns (Repository, Strategy, DI)
2. Add proper logging
3. Write docstrings
4. Keep Single Responsibility
5. Add type hints
