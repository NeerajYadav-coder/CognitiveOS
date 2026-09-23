export interface SiteAdapter {
  platformName: string;
  isMatch(): boolean;
  getPromptInput(): HTMLTextAreaElement | HTMLDivElement | null;
  getSubmitButton(): HTMLButtonElement | null;
  injectEnhancedPrompt(text: string): void;
  onPromptChange(callback: (text: string) => void): void;
  onSubmit(callback: (text: string) => void): void;
}

export abstract class BaseAdapter implements SiteAdapter {
  abstract platformName: string;
  abstract isMatch(): boolean;
  abstract getPromptInput(): HTMLTextAreaElement | HTMLDivElement | null;
  abstract getSubmitButton(): HTMLButtonElement | null;

  injectEnhancedPrompt(text: string): void {
    const input = this.getPromptInput();
    if (input) {
      if (input instanceof HTMLTextAreaElement) {
        input.value = text;
        input.dispatchEvent(new Event("input", { bubbles: true }));
      } else {
        input.innerText = text;
        input.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
  }

  onPromptChange(callback: (text: string) => void): void {
    const input = this.getPromptInput();
    if (input) {
      input.addEventListener("input", (e) => {
        const target = e.target as HTMLElement;
        callback(target.innerText || (target as HTMLTextAreaElement).value);
      });
    }
  }

  onSubmit(callback: (text: string) => void): void {
    const button = this.getSubmitButton();
    if (button) {
      button.addEventListener("click", () => {
        const input = this.getPromptInput();
        if (input) {
          callback(input.innerText || (input as HTMLTextAreaElement).value);
        }
      });
    }
  }
}
