import { useState, useCallback } from "react";

export default function useAsync(fn) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const result = await fn(...args);
        return result;
      } catch (e) {
        setError(e.message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [fn]
  );

  return { execute, loading, error };
}