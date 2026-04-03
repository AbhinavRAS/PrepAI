export default function CodingRound({ onSubmit }) {
  const [code, setCode] = useState("");

  return (
    <div className="p-6">
      <textarea
        className="w-full h-40 border p-2"
        placeholder="Write your code here"
        onChange={(e) => setCode(e.target.value)}
      />
      <button onClick={() => onSubmit(code)}>
        Submit Code
      </button>
    </div>
  );
}
