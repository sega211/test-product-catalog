
import { NextResponse } from "next/server";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function GET(_request: Request, context: RouteContext) {
  const { id } = await context.params;

  if (!/^[1-9]\d*$/.test(id)) {
    return NextResponse.json(
      { error: "Некорректный идентификатор товара" },
      { status: 400 },
    );
  }

  const apiBaseUrl =
    process.env.BACKEND_URL ?? "http://127.0.0.1:8010";

  try {
    const response = await fetch(
      `${apiBaseUrl}/products/${id}/image`,
      { cache: "no-store" },
    );

    if (!response.ok) {
      return NextResponse.json(
        { error: response.status === 404
            ? "У товара нет изображения"
            : "Не удалось загрузить изображение" },
        { status: response.status === 404 ? 404 : 502 },
      );
    }

    const contentType = response.headers.get("content-type");

    if (!contentType || !/^image\/(jpeg|png|webp)$/.test(contentType)) {
      return NextResponse.json(
        { error: "Сервер вернул неподдерживаемый формат изображения" },
        { status: 502 },
      );
    }

    return new Response(await response.arrayBuffer(), {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch {
    return NextResponse.json(
      { error: "Сервер временно недоступен" },
      { status: 502 },
    );
  }
}
