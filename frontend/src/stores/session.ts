import { defineStore } from "pinia";

type SessionUser = {
  id: string;
  email: string;
  displayName: string;
  role: "admin" | "manager" | "analyst" | "viewer";
};

export const useSessionStore = defineStore("session", {
  state: () => ({
    currentUser: null as SessionUser | null,
  }),
  actions: {
    setCurrentUser(user: SessionUser | null) {
      this.currentUser = user;
    },
  },
});
