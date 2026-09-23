import { useState } from "react"
import "../style.css"

function IndexPopup() {
  const [data, setData] = useState("")

  return (
    <div className="w-[400px] p-4 bg-background text-foreground">
      <header className="flex items-center justify-between pb-4 border-b">
        <h1 className="text-lg font-bold text-primary">CognitiveOS</h1>
        <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">v0.1.0</span>
      </header>
      
      <main className="py-6 space-y-4">
        <p className="text-sm text-foreground/80">
          The Cognitive Engine is active. 
          Use the in-page overlay in text inputs to access cognitive features.
        </p>
        
        <div className="p-3 bg-slate-100 dark:bg-slate-800 rounded-md">
          <h2 className="text-sm font-semibold mb-2">Cognitive Pipeline Status</h2>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span>Connected to API Gateway</span>
          </div>
        </div>
      </main>
      
      <footer className="pt-4 border-t text-xs text-center text-foreground/50">
        An Operating Layer Between Human Cognition and AI
      </footer>
    </div>
  )
}

export default IndexPopup
