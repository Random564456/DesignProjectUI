import React, { useEffect, useState, useRef } from "react";

const DataDisplay = ({ inputData }) => {
  const HOSTURL = "ws://0.0.0.0:8000/ws";  // Use ws:// scheme for WebSocket, not http://

  const [messages, setMessages] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = new WebSocket(HOSTURL);

    socketRef.current.onopen = () => {
      console.log("WebSocket connected");
    };

    socketRef.current.onmessage = (event) => {
      console.log("Received:", event.data);
      // Assuming server sends JSON strings
      try {
        const data = JSON.parse(event.data);
        setMessages((prev) => [...prev, data]);
      } catch {
        // If not JSON, just store raw message
        setMessages((prev) => [...prev, event.data]);
      }
    };

    socketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socketRef.current.onclose = () => {
      console.log("WebSocket closed");
    };

    return () => {
      socketRef.current.close();
    };
  }, []);

  // Function to send the first item in inputData over the WebSocket
  const sendMessage = () => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn("WebSocket is not open");
      return;
    }

    if (!inputData || !inputData[0]) {
      console.warn("No inputData to send");
      return;
    }

    // Assuming inputData[0] is an object representing sensor readings
    const message = JSON.stringify(inputData[0]);
    socketRef.current.send(message);
    console.log("Sent:", message);
  };

  return (
    <div>
      <button type="button" onClick={sendMessage}>
        Send Sensor Data
      </button>

      <div>
        <h3>Received Messages:</h3>
        <pre>{JSON.stringify(messages, null, 2)}</pre>
      </div>
    </div>
  );
};

export default DataDisplay;
