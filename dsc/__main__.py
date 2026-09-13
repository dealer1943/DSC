"""python -m dsc  → build MVP into MODEL/active"""
from dsc.runtime import build_mvp


def main() -> None:
    def cb(frac: float, msg: str) -> None:
        bar = int(frac * 30)
        print(f"[{'#'*bar}{'.'*(30-bar)}] {frac*100:5.1f}%  {msg}", flush=True)

    rt = build_mvp(progress=cb, save=True)
    print("revision", rt.revision)
    print("status", rt.status())


if __name__ == "__main__":
    main()
