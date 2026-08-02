export default function Card({ title, children, action }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm">
      {(title || action) && (
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          {title && <h2 className="font-semibold text-gray-800">{title}</h2>}
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="px-6 py-4">{children}</div>
    </div>
  );
}