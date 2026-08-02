export default function Badge({ label, variant = "gray" }) {
  const variants = {
    gray: "bg-gray-100 text-gray-600",
    green: "bg-green-100 text-green-700",
    red: "bg-red-100 text-red-600",
    blue: "bg-blue-100 text-blue-700",
    yellow: "bg-yellow-100 text-yellow-700",
  };

  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${variants[variant]}`}>
      {label}
    </span>
  );
}