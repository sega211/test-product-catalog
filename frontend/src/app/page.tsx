
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import styles from "./page.module.css";

type Product = {
  id: number;
  title: string;
};

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadProducts() {
      try {
        const response = await fetch("/api/products", {
          signal: controller.signal,
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error("Не удалось загрузить каталог");
        }

        const data: unknown = await response.json();

        if (
          !Array.isArray(data) ||
          !data.every(
            (item): item is Product =>
              typeof item.id === "number" &&
              typeof item.title === "string",
          )
        ) {
          throw new Error("Получен некорректный список товаров");
        }

        setProducts(data);
      } catch (err) {
        if (controller.signal.aborted) return;

        setError(
          err instanceof Error
            ? err.message
            : "Не удалось загрузить каталог",
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadProducts();

    return () => controller.abort();
  }, []);

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <Link className={styles.brand} href="/">
          <span className={styles.brandMark} aria-hidden="true">
            К
          </span>
          <span>Каталог</span>
        </Link>
        <span className={styles.headerLabel}>Коллекция товаров</span>
      </header>
      <aside className={styles.demoNotice} aria-label="О проекте">
        <span className={styles.demoNoticeLabel}>
          Демонстрационный проект
        </span>
        <p>
          Сайт создан в рамках тестового задания и демонстрирует реализацию каталога товаров с интеграцией Telegram-бота и объектного хранилища MinIO. Представленные товары и изображения используются в демонстрационных целях.
        </p>
      </aside>
      <section className={styles.hero}>
        <p className={styles.eyebrow}>НАША КОЛЛЕКЦИЯ</p>
        <h1>Товары</h1>
        <p className={styles.subtitle}>
          Всё, что есть в каталоге, — в одном месте.
        </p>
      </section>

      <section className={styles.catalog} aria-label="Каталог товаров">
        <div className={styles.catalogHeading}>
          <h2>Весь каталог</h2>
          {!loading && !error && (
            <span className={styles.count}>
              {products.length}{" "}
              {products.length === 1
                ? "товар"
                : products.length >= 2 &&
                    products.length <= 4
                  ? "товара"
                  : "товаров"}
            </span>
          )}
        </div>

        {loading && (
          <p className={styles.message} role="status">
            Загружаем каталог…
          </p>
        )}

        {error && (
          <div className={styles.message} role="alert">
            <p>{error}</p>
            <button
              className={styles.retryButton}
              onClick={() => window.location.reload()}
            >
              Попробовать снова
            </button>
          </div>
        )}

        {!loading && !error && products.length === 0 && (
          <p className={styles.message}>
            Пока товаров нет. Загляните позже.
          </p>
        )}

        {!loading && !error && products.length > 0 && (
          <div className={styles.grid}>
            {products.map((product) => (
              <article className={styles.card} key={product.id}>
                <div className={styles.imageFrame}>
                  <img
                    className={styles.productImage}
                    src={`/api/products/${product.id}/image`}
                    alt={product.title}
                    loading="lazy"
                    onError={(event) => {
                      const image = event.currentTarget;
                      image.style.display = "none";
                      image.parentElement?.classList.add(
                        styles.noImage,
                      );
                    }}
                  />
                  <span className={styles.imagePlaceholder}>
                    <span aria-hidden="true">◇</span>
                    <span>Фото отсутствует</span>
                  </span>
                </div>

                <div className={styles.cardBody}>
                  <span className={styles.productNumber}>
                    ТОВАР № {product.id}
                  </span>
                  <h3 className={styles.productTitle}>
                    {product.title}
                  </h3>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <footer className={styles.footer}>
        <div className={styles.footerCard}>
          <h2 className={styles.footerTitle}>
            Контакты и площадки
          </h2>

          <div className={styles.socialLinks}>
            <a
              href="https://mnogodeto4ka.ru"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.socialLink}
              title="Основной сайт"
            >
              <span className={styles.socialIcon} aria-hidden="true">
                ↗
              </span>
              <span className={styles.socialText}>
                <strong>Основной сайт</strong>
                <span>Мой сайт и портфолио</span>
              </span>
            </a>

            <a
              href="https://vk.com/mnogodeto4ka_web"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.socialLink}
              title="ВКонтакте"
            >
              <span className={styles.socialIcon} aria-hidden="true">
                VK
              </span>
              <span className={styles.socialText}>
                <strong>ВКонтакте</strong>
                <span>Для быстрых обсуждений</span>
              </span>
            </a>

            <a
              href="https://dzen.ru/3d_shnik"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.socialLink}
              title="Дзен"
            >
              <span className={styles.socialIcon} aria-hidden="true">
                Д
              </span>
              <span className={styles.socialText}>
                <strong>Дзен</strong>
                <span>Видео и материалы по 3D, нейросетям</span>
              </span>
            </a>

            <a
              href="https://github.com/sega211"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.socialLink}
              title="GitHub"
            >
              <span className={styles.socialIcon} aria-hidden="true">
                GH
              </span>
              <span className={styles.socialText}>
                <strong>GitHub</strong>
                <span>Код и технические проекты</span>
              </span>
            </a>
          </div>
        </div>

        <div className={styles.footerAbout}>
          <h2 className={styles.footerTitle}>О проекте</h2>
          <p>
            Демонстрационная работа, созданная в рамках тестового
            задания. Каталог предназначен для демонстрации
            возможностей веб-приложения и интеграции с Telegram.
          </p>
          <p className={styles.copyright}>
            © 2026 · Демонстрационный проект
          </p>
        </div>
      </footer>
    </main>
  );
}
