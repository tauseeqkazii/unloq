import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { globalEvents, EVENTS } from "../lib/events";

export default function GlobalLoader() {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const start = () => setLoading(true);
    const end = () => setLoading(false);

    const unsubStart = globalEvents.on(EVENTS.API_LOADING_START, start);
    const unsubEnd = globalEvents.on(EVENTS.API_LOADING_END, end);

    return () => {
      unsubStart();
      unsubEnd();
    };
  }, []);

  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed top-0 left-0 right-0 h-1.5 z-[100] overflow-hidden bg-transparent pointer-events-none"
        >
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"
            initial={{ x: "-100%" }}
            animate={{ x: "100%" }}
            transition={{
              repeat: Infinity,
              duration: 1.5,
              ease: "easeInOut",
            }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
