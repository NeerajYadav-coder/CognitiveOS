import { BaseAdapter } from "../base";

export class ChatGPTAdapter extends BaseAdapter {
  platformName = "ChatGPT";

  isMatch(): boolean {
    return window.location.hostname.includes("chatgpt.com") || window.location.hostname.includes("openai.com");
  }

  getPromptInput(): HTMLTextAreaElement | HTMLDivElement | null {
    return document.querySelector("#prompt-textarea") || 
           document.querySelector('div[contenteditable="true"]') ||
           document.querySelector('textarea[placeholder*="ChatGPT"]');
  }

  getSubmitButton() {
    return document.querySelector('button[data-testid="send-button"]') || 
           document.querySelector('button[aria-label="Send prompt"]') ||
           document.querySelector('button.absolute.bottom-1.5');
  }
}
