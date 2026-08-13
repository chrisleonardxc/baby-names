import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { getPeople } from "../api/client";
import type { PersonMeta } from "../api/types";

const STORAGE_KEY = "baby-names.viewer";

interface ViewerContextValue {
  people: PersonMeta[];
  viewer: string | null;
  setViewer: (key: string) => void;
}

const ViewerContext = createContext<ViewerContextValue | null>(null);

export function ViewerProvider({ children }: { children: ReactNode }) {
  const [people, setPeople] = useState<PersonMeta[]>([]);
  const [viewer, setViewerState] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));

  useEffect(() => {
    getPeople().then((fetched) => {
      setPeople(fetched);
      if (!viewer && fetched.length > 0) {
        setViewerState(fetched[0].key);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setViewer = (key: string) => {
    setViewerState(key);
    localStorage.setItem(STORAGE_KEY, key);
  };

  const value = useMemo(() => ({ people, viewer, setViewer }), [people, viewer]);

  return <ViewerContext.Provider value={value}>{children}</ViewerContext.Provider>;
}

export function useViewer(): ViewerContextValue {
  const ctx = useContext(ViewerContext);
  if (!ctx) throw new Error("useViewer must be used within a ViewerProvider");
  return ctx;
}
