import { Switch } from "~/components/ui/switch";
import { Label } from "~/components/ui/label";

interface DevModeToggleProps {
  forceAI: boolean;
  onToggle: (enabled: boolean) => void;
}

export function DevModeToggle({ forceAI, onToggle }: DevModeToggleProps) {
  // Only show in development
  if (process.env.NODE_ENV !== "development") {
    return null;
  }

  return (
    <div className="flex items-center space-x-2">
      <Switch 
        id="dev-mode" 
        checked={forceAI} 
        onCheckedChange={onToggle}
      />
      <Label htmlFor="dev-mode" className="text-sm text-muted-foreground">
        Developer Mode (Force AI Products)
      </Label>
    </div>
  );
}
