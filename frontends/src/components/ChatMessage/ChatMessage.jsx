export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`my-1 ${isUser ? "text-right" : "text-left"}`}>
      <div
        className={`${isUser ? "inline-block bg-blue-100 text-black" : "inline-block bg-gray-100 text-black"} p-2 rounded-md max-w-xl break-words`}
      >
        {message.text}
      </div>

      {!isUser && message.role === "assistant" && (
        <div className="mt-1 text-sm text-gray-500">
          {message.confidence !== undefined && (
            <div>Confidence: {message.confidence.toFixed(2)}%</div>
          )}

          {message.sources?.length > 0 && (
            <ul className="list-disc list-inside text-gray-400 mt-1">
              {message.sources.map((s, idx) => (
                <li key={idx}>
                  {s.text} ({s.score.toFixed(2)}%)
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
