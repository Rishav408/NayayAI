# NyayaAI Frontend User Interface Design

## Figure 4: Frontend User Interface Design
*Wireframe and responsive UI layout diagrams showing the complete user interface structure*

```mermaid
graph TB
    %% Main Application Layout
    subgraph "🌐 NyayaAI Application Layout"
        subgraph "📱 Mobile View (sm: 640px)"
            MOBILE_HEADER[📱 Mobile Header<br/>Height: 64px]
            MOBILE_HEADER --> |"Logo + Menu"| MOBILE_NAV[⚖️ NyayaAI Logo + Hamburger Menu]
            MOBILE_HEADER --> |"Theme Toggle"| MOBILE_THEME[🌙 Theme Button]
            
            MOBILE_MAIN[📱 Mobile Main Content<br/>Height: calc(100vh - 64px)]
            MOBILE_MAIN --> |"Full Width"| MOBILE_CHAT[💬 Chat Interface]
            MOBILE_CHAT --> |"Stacked Layout"| MOBILE_SIDEBAR[📋 Conversation Sidebar<br/>Hidden by default]
            MOBILE_CHAT --> |"Primary Content"| MOBILE_CHAT_AREA[💭 Chat Messages Area]
        end
        
        subgraph "💻 Desktop View (md: 768px+)"
            DESKTOP_HEADER[💻 Desktop Header<br/>Height: 64px]
            DESKTOP_HEADER --> |"Logo + Navigation"| DESKTOP_NAV[⚖️ NyayaAI + Features | Chat | About | Contact]
            DESKTOP_HEADER --> |"Actions"| DESKTOP_ACTIONS[🌙 Theme + Start Chat Button]
            
            DESKTOP_MAIN[💻 Desktop Main Content<br/>Height: calc(100vh - 64px)]
            DESKTOP_MAIN --> |"Grid Layout"| DESKTOP_GRID[Grid: 12 columns]
            DESKTOP_GRID --> |"3 columns"| DESKTOP_SIDEBAR[📋 Sidebar<br/>md:col-span-3]
            DESKTOP_GRID --> |"9 columns"| DESKTOP_CHAT[💬 Chat Area<br/>md:col-span-9]
        end
    end
    
    %% Header Components
    subgraph "📋 Header Components"
        HEADER_LOGO[⚖️ Logo<br/>w-9 h-9 + NyayaAI Text]
        HEADER_NAV[🧭 Navigation Menu<br/>Features | Chat | About | Contact]
        HEADER_THEME[🌙 Theme Toggle<br/>Dark/Light Mode]
        HEADER_CTA[🚀 Start Chat Button<br/>Gradient Background]
    end
    
    %% Sidebar Components
    subgraph "📋 Sidebar Components"
        SIDEBAR_HEADER[📝 Conversations Header<br/>Title + New Chat Button]
        SIDEBAR_LIST[📜 Conversation List<br/>Scrollable History]
        SIDEBAR_ACTIONS[⚙️ Sidebar Actions<br/>Rename | Delete Buttons]
        
        SIDEBAR_HEADER --> |"➕ New Chat"| NEW_CHAT_BTN[New Chat Button<br/>Gradient Background]
        SIDEBAR_LIST --> |"Thread Items"| THREAD_ITEMS[Thread Items<br/>Title + Message Count]
        SIDEBAR_ACTIONS --> |"Actions"| ACTION_BTNS[Rename | Delete<br/>Secondary Buttons]
    end
    
    %% Chat Interface Components
    subgraph "💬 Chat Interface Components"
        CHAT_HEADER[📊 Chat Header<br/>Ask NyayaAI + Status]
        CHAT_MESSAGES[💭 Messages Container<br/>Scrollable Area]
        CHAT_COMPOSER[✏️ Message Composer<br/>Input + Tools + Send]
        
        CHAT_HEADER --> |"Status Info"| STATUS_INFO[Gemini • LangChain • Web Search]
        CHAT_HEADER --> |"Test Button"| TEST_BTN[Test Connection Button]
        
        CHAT_MESSAGES --> |"Message Types"| MSG_TYPES[User Messages | AI Messages | Loading States]
        MSG_TYPES --> |"User"| USER_MSG[👤 User Message<br/>Right-aligned, Slate Background]
        MSG_TYPES --> |"AI"| AI_MSG[🤖 AI Message<br/>Left-aligned, White Background]
        MSG_TYPES --> |"Loading"| LOADING_MSG[⏳ Loading Message<br/>Animated Dots]
        
        CHAT_COMPOSER --> |"Input Area"| INPUT_AREA[📝 Textarea<br/>Auto-resize, Placeholder]
        CHAT_COMPOSER --> |"Tool Buttons"| TOOL_BTNS[🛠️ Tool Buttons<br/>Upload | Mic | Search]
        CHAT_COMPOSER --> |"Send Button"| SEND_BTN[➤ Send Button<br/>Gradient Background]
    end
    
    %% Message Components
    subgraph "💭 Message Components"
        MSG_STRUCTURE[📦 Message Structure]
        MSG_STRUCTURE --> |"Avatar"| MSG_AVATAR[👤 Avatar<br/>User: U | AI: AI]
        MSG_STRUCTURE --> |"Content"| MSG_CONTENT[📝 Message Content]
        MSG_STRUCTURE --> |"Metadata"| MSG_META[📊 Message Metadata]
        
        MSG_CONTENT --> |"Label"| MSG_LABEL[🏷️ Message Label<br/>You | NyayaAI]
        MSG_CONTENT --> |"Body"| MSG_BODY[📄 Message Body<br/>Formatted Text]
        MSG_CONTENT --> |"Search Info"| SEARCH_INFO[🔍 Search Information<br/>Used/Not Used + Reason]
        MSG_CONTENT --> |"Sources"| SOURCES[📚 Sources Section<br/>Links to References]
        
        SEARCH_INFO --> |"Search Used"| SEARCH_USED[✅ Enhanced with web search<br/>Green Badge]
        SEARCH_INFO --> |"Search Not Used"| SEARCH_NOT_USED[ℹ️ AI knowledge only<br/>Blue Badge]
        SEARCH_INFO --> |"Forced Search"| FORCED_SEARCH[🔄 Forced web search<br/>Orange Badge]
    end
    
    %% Tool Components
    subgraph "🛠️ Tool Components"
        FILE_UPLOAD[📁 File Upload Tool]
        VOICE_INPUT[🎤 Voice Input Tool]
        SEARCH_TOGGLE[🔍 Search Toggle Tool]
        
        FILE_UPLOAD --> |"File Types"| FILE_TYPES[PDF | TXT | DOC | DOCX<br/>Max 10MB]
        FILE_UPLOAD --> |"Upload Status"| UPLOAD_STATUS[📊 Upload Status<br/>Success | Error | Processing]
        FILE_UPLOAD --> |"File Chip"| FILE_CHIP[📄 File Chip<br/>Filename + Remove Button]
        
        VOICE_INPUT --> |"Status"| VOICE_STATUS[🎤 Voice Input<br/>Coming Soon]
        
        SEARCH_TOGGLE --> |"States"| SEARCH_STATES[🔍 Search States<br/>Enabled | Disabled]
        SEARCH_STATES --> |"Enabled"| SEARCH_ENABLED[🟢 Search Enabled<br/>Highlighted State]
        SEARCH_STATES --> |"Disabled"| SEARCH_DISABLED[⚪ Search Disabled<br/>Default State]
    end
    
    %% Error and Status Components
    subgraph "⚠️ Error and Status Components"
        ERROR_BANNER[⚠️ Error Banner<br/>Connection Issues]
        STATUS_MESSAGES[📊 Status Messages<br/>Success | Warning | Error]
        LOADING_INDICATORS[⏳ Loading Indicators<br/>Spinner | Dots | Progress]
        
        ERROR_BANNER --> |"Types"| ERROR_TYPES[Network Error | API Error | Validation Error]
        STATUS_MESSAGES --> |"Upload Status"| UPLOAD_MSGS[Upload Success | Upload Failed | Processing]
        LOADING_INDICATORS --> |"Chat Loading"| CHAT_LOADING[💬 Chat Loading<br/>Animated Dots]
    end
    
    %% Responsive Breakpoints
    subgraph "📱 Responsive Breakpoints"
        BREAKPOINTS[📐 Breakpoint System]
        BREAKPOINTS --> |"Mobile"| MOBILE_BP[sm: 640px<br/>Single Column Layout]
        BREAKPOINTS --> |"Tablet"| TABLET_BP[md: 768px<br/>Sidebar + Chat Layout]
        BREAKPOINTS --> |"Desktop"| DESKTOP_BP[lg: 1024px<br/>Full Layout]
        
        MOBILE_BP --> |"Layout"| MOBILE_LAYOUT[Full Width Chat<br/>Hidden Sidebar]
        TABLET_BP --> |"Layout"| TABLET_LAYOUT[3/9 Grid Split<br/>Visible Sidebar]
        DESKTOP_BP --> |"Layout"| DESKTOP_LAYOUT[3/9 Grid Split<br/>Full Features]
    end
    
    %% Theme System
    subgraph "🎨 Theme System"
        THEME_SYSTEM[🌓 Dark/Light Theme]
        THEME_SYSTEM --> |"Light Theme"| LIGHT_THEME[☀️ Light Theme<br/>Slate Backgrounds | Dark Text]
        THEME_SYSTEM --> |"Dark Theme"| DARK_THEME[🌙 Dark Theme<br/>Black Backgrounds | Light Text]
        
        LIGHT_THEME --> |"Colors"| LIGHT_COLORS[bg-slate-50 | text-slate-800 | border-slate-200]
        DARK_THEME --> |"Colors"| DARK_COLORS[bg-black | text-slate-100 | border-slate-800]
        
        THEME_SYSTEM --> |"Persistence"| THEME_STORAGE[💾 localStorage<br/>User Preference]
    end
    
    %% Styling
    classDef mobileLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef desktopLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef componentLayer fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef messageLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef toolLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef errorLayer fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef themeLayer fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef responsiveLayer fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    
    class MOBILE_HEADER,MOBILE_NAV,MOBILE_THEME,MOBILE_MAIN,MOBILE_CHAT,MOBILE_SIDEBAR,MOBILE_CHAT_AREA mobileLayer
    class DESKTOP_HEADER,DESKTOP_NAV,DESKTOP_ACTIONS,DESKTOP_MAIN,DESKTOP_GRID,DESKTOP_SIDEBAR,DESKTOP_CHAT desktopLayer
    class HEADER_LOGO,HEADER_NAV,HEADER_THEME,HEADER_CTA,SIDEBAR_HEADER,SIDEBAR_LIST,SIDEBAR_ACTIONS,CHAT_HEADER,CHAT_MESSAGES,CHAT_COMPOSER componentLayer
    class MSG_STRUCTURE,MSG_AVATAR,MSG_CONTENT,MSG_META,MSG_LABEL,MSG_BODY,SEARCH_INFO,SOURCES,USER_MSG,AI_MSG,LOADING_MSG messageLayer
    class FILE_UPLOAD,VOICE_INPUT,SEARCH_TOGGLE,FILE_TYPES,UPLOAD_STATUS,FILE_CHIP,VOICE_STATUS,SEARCH_STATES,SEARCH_ENABLED,SEARCH_DISABLED toolLayer
    class ERROR_BANNER,STATUS_MESSAGES,LOADING_INDICATORS,ERROR_TYPES,UPLOAD_MSGS,CHAT_LOADING errorLayer
    class THEME_SYSTEM,LIGHT_THEME,DARK_THEME,LIGHT_COLORS,DARK_COLORS,THEME_STORAGE themeLayer
    class BREAKPOINTS,MOBILE_BP,TABLET_BP,DESKTOP_BP,MOBILE_LAYOUT,TABLET_LAYOUT,DESKTOP_LAYOUT responsiveLayer
```

## Detailed UI Component Specifications

### 1. **Header Layout**
```
┌─────────────────────────────────────────────────────────────────┐
│ ⚖️ NyayaAI    Features | Chat | About | Contact    🌙 Start Chat │
│ (Logo)        (Navigation)                        (Theme) (CTA)  │
└─────────────────────────────────────────────────────────────────┘
Height: 64px | Sticky | Backdrop Blur | Border Bottom
```

### 2. **Desktop Layout (md: 768px+)**
```
┌─────────────────────────────────────────────────────────────────┐
│                         Header (64px)                          │
├─────────────────┬───────────────────────────────────────────────┤
│   Sidebar       │              Chat Area                        │
│   (3 cols)      │              (9 cols)                        │
│                 │                                               │
│ ┌─────────────┐ │ ┌─────────────────────────────────────────┐   │
│ │Conversations│ │ │            Chat Messages                 │   │
│ │   + New     │ │ │                                         │   │
│ │             │ │ │  👤 User: What is Section 420 IPC?      │   │
│ │ 📋 Chat 1   │ │ │  🤖 AI: Section 420 deals with...      │   │
│ │ 📋 Chat 2   │ │ │                                         │   │
│ │ 📋 Chat 3   │ │ └─────────────────────────────────────────┘   │
│ │             │ │                                               │
│ │ Rename Delete│ │ ┌─────────────────────────────────────────┐   │
│ └─────────────┘ │ │            Message Composer              │   │
│                 │ │  📁 🎤 🔍  Type your question...  [➤]   │   │
│                 │ └─────────────────────────────────────────┘   │
└─────────────────┴───────────────────────────────────────────────┘
```

### 3. **Mobile Layout (sm: 640px)**
```
┌─────────────────────────────────────────────────────────────────┐
│ ⚖️ NyayaAI                                        🌙            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    Chat Messages Area                           │
│                                                                 │
│  👤 User: What is Section 420 IPC?                             │
│  🤖 AI: Section 420 of the Indian Penal Code...               │
│                                                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  📁 🎤 🔍  Type your question...                    [➤]       │
└─────────────────────────────────────────────────────────────────┘
```

### 4. **Message Component Structure**
```
┌─────────────────────────────────────────────────────────────────┐
│ 👤 U  │ You                                                      │
│       │ What is the difference between civil and criminal law?  │
│       │                                                          │
│       │ [ℹ️ AI knowledge only (basic legal question)]            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🤖 AI │ NyayaAI                                                  │
│       │ Civil law deals with disputes between individuals...    │
│       │                                                          │
│       │ [✅ Enhanced with web search (recent case law)]         │
│       │                                                          │
│       │ ┌─────────────────────────────────────────────────────┐ │
│       │ │ Sources consulted:                                  │ │
│       │ │ 🔗 Supreme Court of India - Civil Law Cases        │ │
│       │ │ 🔗 Indian Penal Code - Criminal Law Provisions     │ │
│       │ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 5. **Tool Components**
```
┌─────────────────────────────────────────────────────────────────┐
│ Tool Buttons:                                                   │
│                                                                 │
│ 📁 Upload Document  🎤 Voice Input  🔍 Web Search Toggle      │
│    (PDF, DOC, TXT)    (Coming Soon)    (Enabled/Disabled)     │
│                                                                 │
│ File Upload Status:                                             │
│ ✅ contract.pdf uploaded successfully                           │
│                                                                 │
│ Search Toggle States:                                           │
│ 🔍 Search Enabled (Highlighted)                                │
│ ⚪ Search Disabled (Default)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6. **Responsive Breakpoint System**
```
Mobile (sm: 640px):
├── Single column layout
├── Hidden sidebar (toggle menu)
├── Full-width chat interface
└── Stacked navigation

Tablet (md: 768px):
├── 3/9 column grid split
├── Visible sidebar
├── Side-by-side layout
└── Full navigation menu

Desktop (lg: 1024px):
├── 3/9 column grid split
├── Full sidebar functionality
├── All features visible
└── Optimized spacing
```

### 7. **Theme System Implementation**
```
Light Theme:
├── Background: bg-slate-50
├── Text: text-slate-800
├── Borders: border-slate-200
├── Cards: bg-white
└── Shadows: shadow-soft

Dark Theme:
├── Background: bg-black
├── Text: text-slate-100
├── Borders: border-slate-800
├── Cards: bg-white/5
└── Shadows: shadow-soft

Theme Persistence:
├── localStorage.getItem('theme')
├── System preference detection
├── Automatic theme switching
└── Manual toggle control
```

## Key UI Features

### **Accessibility Features**
- **Keyboard Navigation**: Full keyboard support for all interactive elements
- **Screen Reader Support**: Proper ARIA labels and semantic HTML
- **Color Contrast**: WCAG compliant color combinations
- **Focus Management**: Clear focus indicators and logical tab order

### **Performance Optimizations**
- **Lazy Loading**: Messages loaded on demand
- **Virtual Scrolling**: Efficient rendering of long conversation histories
- **Debounced Input**: Optimized search and input handling
- **Efficient Re-renders**: Minimal DOM updates with proper state management

### **User Experience Enhancements**
- **Auto-resize Textarea**: Dynamic height adjustment
- **Typing Indicators**: Real-time feedback during AI processing
- **Message Timestamps**: Conversation timeline tracking
- **Copy/Share Features**: Easy content sharing capabilities

This UI design provides a comprehensive, responsive, and user-friendly interface for the NyayaAI legal assistant platform with modern design principles and accessibility considerations.
