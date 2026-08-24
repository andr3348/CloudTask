import { TaskList } from "@/components/tasks/task-list";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col bg-background">
      <header className="sticky top-0 z-30 border-b border-border/50 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto max-w-5xl px-6 py-5">
          <h1 className="text-3xl font-bold tracking-tight">CloudTask</h1>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-6">
        <TaskList />
      </main>
    </div>
  );
}
